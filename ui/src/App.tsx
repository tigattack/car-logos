import { useEffect, useState } from 'react'
import { Company, ICompany } from './components/Company'
import { imgDbMockFactory } from '../tests/imgdb.mock'

import './App.css'

export const IMGDB_API_URL = 'http://localhost:5000/api/companies';

const App = () => {
  const tempCompanyData: ICompany[] = imgDbMockFactory(100);
  // const [companyData, setCompanyData] = useState<ICompany[]>([]);

  // useEffect(() => {
  //   fetch(IMGDB_API_URL)
  //     .then((response) => response.json())
  //     .then((data) => setCompanyData(data));

  // });
  console.log(tempCompanyData);

  return (
    <>
      <h1>Vehicle Logo DB</h1>

      <div className="container">
        {tempCompanyData.map((company) => <Company company={company} />)}
      </div>
    </>
  )
}

export default App
